pipeline {
    agent any
    stages {
        stage('Code Analysis') {
            steps {
                script {
                    def response = sh(script: """
                        echo "Hello"
                    """, returnStdout: true)
                    echo "Analysis Results: ${response}"
                }
            }
        }
    }
}