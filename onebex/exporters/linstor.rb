# -------------------------------------------------------------------------- #
# OpenNebula Driver for Linstor                                              #
# Copyright 2026 LINBIT USA LLC                                              #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
#--------------------------------------------------------------------------- #

require 'open3'

module OneBEX

    module Exporters

        # LINSTOR exporter for the CBT snapshots of LINSTOR resources.
        #
        # The linstor TM driver (prebackup) takes the snapshot, starts its CBT
        # session (the snapshot restored into a temporary resource, readable
        # read-only on this host) and removes both once the export finished.
        # This exporter only reads the session's DRBD device.
        class LINSTOR

            # Stores shared exporter configuration and logging dependencies.
            def initialize(config:, logger:)
                @config = config
                @logger = logger
            end

            # ----------------------------------------------------------------
            # Start LINSTOR exporter
            # Checks the DRBD device of the CBT session.
            #
            # Transfer hash attributes used by this exporter:
            #   Read:
            #     :transfer_id - unique transfer identifier used for logs
            #     :source      - DRBD device of the CBT session on this host
            #     :format      - transfer format returned by info
            #     :disk        - disk export data from interactive_exports.json
            #
            #   :disk attributes read:
            #     mode       - full or incremental
            #     extents    - file with one "<start> <length> <dirty> <zero>"
            #                  line (bytes, flags 0 or 1) per extent, they
            #                  cover the device without gaps; required for
            #                  incremental exports, without it a full export
            #                  is the whole device
            #     size_bytes - device size in bytes as the CBT session reported
            #                  it, read from the device if not set
            #
            #   Written:
            #     :device      - block device used by reads
            #     :mode        - normalized export mode
            #     :format      - normalized transfer format
            #     :extents     - extents file, empty for the whole device
            #     :size        - device size in bytes, the export size
            # ----------------------------------------------------------------
            def start(xfr)
                disk = xfr[:disk] || {}

                xfr[:device]  = xfr[:source].to_s
                xfr[:mode]    = (disk['mode'] || 'full').to_s.downcase
                xfr[:format]  = (xfr[:format] || 'raw').to_s
                xfr[:extents] = disk['extents'].to_s

                raise 'Missing LINSTOR source device' if xfr[:device].empty?

                unless File.exist?(xfr[:device])
                    raise "LINSTOR source device not found: #{xfr[:device]}"
                end

                unless File.blockdev?(xfr[:device])
                    raise "LINSTOR source is not a block device: #{xfr[:device]}"
                end

                unless ['full', 'incremental'].include?(xfr[:mode])
                    raise "Unsupported LINSTOR export mode: #{xfr[:mode]}"
                end

                if (xfr[:mode] == 'incremental' || !xfr[:extents].empty?) &&
                   !File.file?(xfr[:extents])
                    raise "LINSTOR extents file not found: #{xfr[:extents]}"
                end

                xfr[:size] = device_size_bytes(xfr, disk)

                @logger.info(
                    "Using LINSTOR source for #{xfr[:transfer_id]}: " \
                    "#{xfr[:device]}, mode=#{xfr[:mode]}"
                )

                true
            rescue StandardError => e
                @logger.error(
                    "Failed to start LINSTOR transfer #{xfr[:transfer_id]}: " \
                    "#{e.message}"
                )

                raise
            end

            # ----------------------------------------------------------------
            # Get block map
            # Returns the extents of the CBT snapshot as OneBEX extent entries,
            # as ovirt-imageio reports them: dirty ones changed since the last
            # backup (all for a full export), zero ones were never written.
            # Without extents file the whole device.
            # ----------------------------------------------------------------
            def blocks(xfr)
                return [extent(0, xfr[:size], true, false)] if xfr[:extents].empty?

                File.foreach(xfr[:extents]).map do |line|
                    start, length, dirty, zero = line.split.map {|value| Integer(value, 10) }

                    extent(start, length, dirty == 1, zero == 1)
                end
            rescue StandardError => e
                @logger.error(
                    "Failed to get LINSTOR block map for #{xfr[:transfer_id]}: " \
                    "#{e.message}"
                )

                raise
            end

            # ----------------------------------------------------------------
            # Read disk data
            # Reads a byte range from the DRBD device and returns binary data.
            # ----------------------------------------------------------------
            def data(xfr, range)
                expected = range[:length].to_i
                offset   = range[:start].to_i

                if expected <= 0 || offset < 0 || offset + expected > xfr[:size]
                    raise "Invalid read range #{range} for a disk of #{xfr[:size]} bytes"
                end

                data = File.open(xfr[:device], 'rb') {|io| io.pread(expected, offset).b }

                if data.bytesize != expected
                    raise "LINSTOR read returned #{data.bytesize} bytes, " \
                          "expected #{expected}"
                end

                data
            rescue StandardError => e
                @logger.error(
                    "Failed to read LINSTOR data for #{xfr[:transfer_id]}: " \
                    "#{e.message}"
                )

                raise
            end

            # ----------------------------------------------------------------
            # Finish LINSTOR exporter
            # Completes the export; the TM driver removes session and snapshot.
            # ----------------------------------------------------------------
            def finish(_xfr, **)
                true
            end

            # ----------------------------------------------------------------
            # Get transfer info
            # Returns virtual disk size in MiB and the transfer format.
            # ----------------------------------------------------------------
            def info(xfr)
                size_mib = (xfr[:size] + 1024 * 1024 - 1) / (1024 * 1024)

                {
                    :SIZE   => size_mib,
                    :FORMAT => xfr[:format]
                }
            end

            # ----------------------------------------------------------------
            # Helpers
            # ----------------------------------------------------------------

            private

            def extent(start, length, dirty, zero)
                {
                    :start  => start,
                    :length => length,
                    :dirty  => dirty,
                    :zero   => zero,
                    :hole   => false
                }
            end

            # Returns the device size in bytes, as the CBT session reported it or
            # read from the device.
            def device_size_bytes(xfr, disk)
                size = disk['size_bytes'].to_i
                return size if size > 0

                stdout, stderr, status = Open3.capture3(
                    'blockdev', '--getsize64', xfr[:device]
                )

                raise "Could not get the size of #{xfr[:device]}: #{stderr}" \
                    unless status.success?

                stdout.to_i
            end

        end

    end

end

# OneBEX loads every file of the exporters directory and the exporters register themselves
# (OpenNebula 7.4.2+), older versions don't support third party exporters
if OneBEX::Exporters.respond_to?(:register)
    OneBEX::Exporters.register('linstor', OneBEX::Exporters::LINSTOR)
end
