pipeline {
  agent any
  stages {
    stage('Hola') {
      steps { echo 'Jenkins funciona' }
    }
  }
  post {
    success {
      slackSend channel: '#ci-crowdstarter',
                color: 'good',
                message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} pasó (${env.BRANCH_NAME})\n${env.BUILD_URL}"
    }
    failure {
      slackSend channel: '#ci-crowdstarter',
                color: 'danger',
                message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} falló (${env.BRANCH_NAME})\n${env.BUILD_URL}"
    }
  }
}
