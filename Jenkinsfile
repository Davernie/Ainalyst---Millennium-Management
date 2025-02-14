// remove <> when replacing API_ENDPOINT

pipeline {
    agent any
    stages {
        stage('Get Code') {
            steps {
                // Access the git repo 
                git url: 'git repo url', branch: 'main'
            }
        }
        stage('Code Analysis') {
            steps {
                script {
                    // Read the code from a file in the repository
                    def code = readFile('Example.py')

                    // Send the code to the API
                    def response = sh(script: """
                        curl -X POST <API_ENDPOINT> -H "Content-Type: application/json" -d '{"code": ${code}}'
                    """, returnStdout: true)

                    echo "Analysis Results: ${response}"
                }
            }
        }
    }
}