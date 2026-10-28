pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    stages {
        stage('Instalar dependencias') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Verificar Django') {
            steps {
                sh '''
                    . venv/bin/activate
                    python manage.py check
                '''
            }
        }

        stage('Ejecutar pruebas') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    python -m pytest -v --junitxml=reports/pytest.xml
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/pytest.xml', allowEmptyResults: true
        }
        success {
            slackSend channel: '#ci-crowdstarter', color: 'good',
                message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} pasó (${env.BRANCH_NAME})\n${env.BUILD_URL}"
        }
        failure {
            slackSend channel: '#ci-crowdstarter', color: 'danger',
                message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} falló (${env.BRANCH_NAME})\n${env.BUILD_URL}"
        }
    }
}
