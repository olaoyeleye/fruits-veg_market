pipeline {
    agent any
        environment {
            AWS_ACCESS_KEY_ID     = credentials ('AWS_ACCESS_KEY_ID')
            AWS_SECRET_ACCESS_KEY = credentials ('AWS_SECRET_ACCESS_KEY') 
            AWS_ECR_REGION        = 'eu-west-2' // London
            AWS_ACCOUNT_ENV       = "647743454395"   
            CONFIGMAP_BASE_S3     = "techbleat-terraform-state-cynwumoye"
            REPOSITORY_NAME       = "p_fruits-veg_market"  
            PROJECT_NAME         = "fruits-veg_market-app"      
            
            ECR_REPO              = "${AWS_ACCOUNT_ENV}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${REPOSITORY_NAME}"
                  } 

     parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: "DEV\nSTAGE\nPROD",
            description: 'Select the environment to deploy to'
        )
    }
    stages {
       
        stage("Build & Tag Docker Image for Java App") {
            steps {
# 1. Add jenkins user to the docker group
                sh"sudo usermod -aG docker jenkins"
                sh"sudo systemctl restart jenkins
                // Building Docker Image for ${REPOSITORY_NAME}
                sh "echo building Docker image for ${REPOSITORY_NAME}"
                sh "sudo docker build -t ${REPOSITORY_NAME}:${BUILD_NUMBER} --build-arg SPRING_DATA_CASSANDRA_CONTACT_POINTS=54.187.44.138 ."

                // Tag Docker Image for ${REPOSITORY_NAME}
                sh "echo tagging Docker image for ${REPOSITORY_NAME}:${BUILD_NUMBER}"
                sh "sudo docker tag ${REPOSITORY_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${BUILD_NUMBER}"
            }
        }

        stage('Push Docker Image to ECR') {
            when {
                anyOf {
                branch "dev"  
                branch "prod"
                }
            }
            steps {
                sh "echo Retrieve authentication token and authenticate Docker client to ECR."
                sh """
                    aws ecr get-login-password --region ${AWS_ECR_REGION} |  docker login --username AWS --password-stdin ${ECR_REPO}

                    echo 'Pushing ${REPOSITORY_NAME} Docker Image to ECR'
                    docker push ${ECR_REPO}:${BUILD_NUMBER}
                """
            }
        }
        stage('Download ConfigMap from S3 and Update Deploy file') { // Dev Cluster @ eu-west-2
            when {
                anyOf {
                branch "dev"
                branch "prod"
                }
            }
            steps {

               sh  """  
                   AWS_DEFAULT_REGION=US-WEST-2 aws s3 cp s3://${CONFIGMAP_BASE_S3}/${PROJECT_NAME}/config/${env.BRANCH_NAME}/${CONFIG_MAP_FILE} .

                   
                   #sed -i 's/VERSION_AUTO_REPLACE/${BUILD_NUMBER}/g' ${deploy_yml} 
                   #sed -i 's|var_RAM_Memory|${RAM_Memory} |g' ${deploy_yml} 
                """
           }
        }
       
        stage('Deploy Image to EKS dev cluster') { // Dev Cluster @ eu-west-2
            when {
                anyOf {
                branch "dev"
                }
            }
            steps {
                sh  """ 
                    /usr/local/bin/aws eks update-kubeconfig --name CynWumOye_CYO-cluster --region eu-west-1                    kubectl get pods --namespace ${EKS_CONFIG['DEV'].NAMESPACE}
                    kubectl apply -f ${CONFIG_MAP_FILE} --namespace ${EKS_CONFIG['DEV'].NAMESPACE}
                    kubectl apply -f ${deploy_yml}  --namespace ${EKS_CONFIG['DEV'].NAMESPACE}
                    kubectl apply -f service.yml --namespace ${EKS_CONFIG['DEV'].NAMESPACE}
                    kubectl apply -f ingress.yml --namespace ${EKS_CONFIG['DEV'].NAMESPACE}

                    kubectl get pods --namespace ${EKS_CONFIG['DEV'].NAMESPACE}
                    kubectl get svc --namespace ${EKS_CONFIG['DEV'].NAMESPACE}
                    kubectl -n ${EKS_CONFIG['DEV'].NAMESPACE} get deploy
                    kubectl -n ${EKS_CONFIG['DEV'].NAMESPACE} get ingress
                """
           }
        }   
        stage("Deployment Approval") {
            when {
                anyOf {
                branch "prod"
            }
        }
            steps {
                // Deployment Approval
                sh "echo ${env.BRANCH_NAME} Deployment Approval"
                emailext body: "A ${env.BRANCH_NAME} build is awaiting approval ${env.JOB_URL}", 
                    subject: "A ${env.BRANCH_NAME} deployment awaiting approval: ${currentBuild.fullDisplayName}",
                    from: "olaoyeleye@yahoo.co.uk",
                    to: "olaoyeleye@yahoo.co.uk"
                timeout(time: 120, unit: 'MINUTES') {
                    input "Deploy to ${env.BRANCH_NAME} env?"
                }
           }
        }
        }       
    }


    post {
        always {
            echo 'One way or another, I have finished'
          // sh 'sudo rm -rf /var/lib/jenkins/workspace/base-alarms-integration_dev-test'
          //  sh 'sudo rm -rf  ${_PWD}/app'
          //  sh "sudo docker system prune -a --volumes -f"
            deleteDir() /* clean up our workspace */
        }
        success {
            echo 'I succeeded!'
            emailext body: "Pipeline was successfully built ${env.BUILD_URL}",
                subject: "Successful Pipeline: ${currentBuild.fullDisplayName}",
                from: "olaoyeleye@yahoo.co.uk",
                to: "olaoyeleye@yahoo.co.uk"
        }
        aborted {
            echo 'I aborted!'
            emailext body: "Pipeline was aborted: find details at ${env.BUILD_URL}",
                subject: "Aborted Pipeline: ${currentBuild.fullDisplayName}",
                from: "olaoyeleye@yahoo.co.uk",
                to: "olaoyeleye@yahoo.co.uk"
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
            emailext body: "Pipeline Build Failure ${env.BUILD_URL}",
                subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
                from: "olaoyeleye@yahoo.co.uk",
                to: "olaoyeleye@yahoo.co.uk"
        }
        changed {
            echo 'Things were different before...'
        }
    }

