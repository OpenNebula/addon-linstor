if git rev-parse --verify HEAD >/dev/null 2>&1
then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Redirect output to stderr.
exec 1>&2

changed_python=$(git diff-index --diff-filter=ACMRT --name-only HEAD -- | xargs file | grep Python | cut -d: -f1)

if [ -n "$changed_python" ]
then
  set -x
	for file in $changed_python; do
	  autoflake --remove-unused-variables --remove-all-unused-imports -i $file;
	  isort -y $file;
	  black $file;
	done
  set +x
fi
