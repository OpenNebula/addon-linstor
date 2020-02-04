pipeline {
    parameters {
        string(
            name: 'PYTHON_LINSTOR_URL',
            defaultValue: 'https://github.com/LINBIT/linstor-api-py.git',
            description: 'git url for python-linstor')
    }
    agent { docker { image 'python:3.5.1' } }
    stages {
        stage('VENV') {
            steps {
                sh 'python -m venv venv'
            }
        }
        stage('Install python-linstor') {
            steps {
                dir('python-linstor') {
                    git url: "${params.PYTHON_LINSTOR_URL}"
                    sh '../venv/bin/python setup.py install'
                }
            }
        }
        stage('Checkout') {
            steps {
                dir('linstor-opennebula') {
                    checkout scm
                }
            }
        }
        stage('Test') {
            steps {
                dir('linstor-opennebula') {
                    sh '../venv/bin/python setup.py test'
                }
            }
        }
    }
}
