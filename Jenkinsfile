pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

    triggers {
        githubPush()
    }

    environment {
        PLAYWRIGHT_BROWSERS_PATH = "${env.JENKINS_HOME}/playwright-browsers"
        BASE_URL = 'http://127.0.0.1:8016'
    }

    stages {
        stage('Limpiar reportes anteriores') {
            steps {
                dir('reports') {
                    deleteDir()
                }
            }
        }

        stage('Instalar dependencias') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Instalar navegador') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m playwright install chromium
                '''
            }
        }

        stage('Verificar Django') {
            steps {
                sh '''
                    . venv/bin/activate
                    python manage.py check
                    python manage.py makemigrations --check --dry-run
                    python manage.py migrate --noinput
                '''
            }
        }

        stage('Pruebas unitarias e integración') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    python -m pytest campaigns/tests -v --junitxml=reports/pytest.xml
                '''
            }
        }

        stage('Pruebas E2E/UI') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports/screenshots
                    python -m pytest e2e -v --junitxml=reports/e2e-junit.xml --html=reports/e2e.html --self-contained-html
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/*.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**/*',
                allowEmptyArchive: true,
                fingerprint: true
        }
        success {
            slackSend channel: '#ci-crowdstarter', color: 'good',
                message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} pasó (${env.BRANCH_NAME ?: 'main'})\n${env.BUILD_URL}"
        }
        failure {
            slackSend channel: '#ci-crowdstarter', color: 'danger',
                message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} falló (${env.BRANCH_NAME ?: 'main'})\nArtefactos (screenshots y reporte): ${env.BUILD_URL}artifact/reports/\n${env.BUILD_URL}"
        }
    }
}
