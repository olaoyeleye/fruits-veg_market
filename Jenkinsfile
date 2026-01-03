pipeline {
    agent any
        environment {
            AWS_ACCESS_KEY_ID     = credentials ('AWS_ACCESS_KEY_ID')
            AWS_SECRET_ACCESS_KEY = credentials ('AWS_SECRET_ACCESS_KEY') 
            AWS_ECR_REGION        = 'eu-west-1' 
            AWS_ACCOUNT_ENV       = "647743454395"   
            CONFIGMAP_BASE_S3     = "techbleat-terraform-state-cynwumoye"
            REPOSITORY_NAME       = "p_fruits-veg_market"  
            PROJECT_NAME         = "fruits-veg_market-app"      
            CONFIG_MAP_FILE       = "configmap-fruits-veg_market.yml"  
            ECR_REPO              = "${AWS_ACCOUNT_ENV}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${REPOSITORY_NAME}"
            NAMESPACE_DEV         = "cynwumoye"

                  } 
//"configmap-${PROJECT_NAME}-${ENVIRONMENT}.yml"=
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


                // Building Docker Image for ${REPOSITORY_NAME}
                sh "echo building Docker image for ${REPOSITORY_NAME}"
                sh "docker build -t ${REPOSITORY_NAME}:${BUILD_NUMBER} ."

                // Tag Docker Image for ${REPOSITORY_NAME}
                sh "echo tagging Docker image for ${REPOSITORY_NAME}:${BUILD_NUMBER}"
                sh "docker tag ${REPOSITORY_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${BUILD_NUMBER}"
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
                sh """#!/bin/bash
                    # 1. Download files
                    export AWS_DEFAULT_REGION=eu-west-1
                    aws s3 cp s3://${CONFIGMAP_BASE_S3}/${PROJECT_NAME}/cynwumoye-app-manifest/${env.BRANCH_NAME}/deploy.yml . || exit 1

                    # 2. Perform replacements
                    # Using double quotes for the sed command so Jenkins variables work
                    sed -i "s/VERSION_AUTO_REPLACE/${env.BUILD_NUMBER}/g" deploy.yml
                    sed -i "s|var_img|${ECR_REPO}|g" deploy.yml

                    # 3. Debugging (The part you are missing)
                    echo "--- CURRENT DIRECTORY CONTENTS ---"
                    ls -ltar
                    
                    echo "--- UPDATED DEPLOY.YML ---"
                    if [ -f deploy.yml ]; then
                        cat deploy.yml
                    else
                        echo "ERROR: deploy.yml not found!"
                        exit 1
                    fi
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
                    aws eks update-kubeconfig --name CynWumOye_CYO-cluster --region eu-west-1
                    
                    kubectl get pods --namespace ${NAMESPACE_DEV}
                    kubectl create namespace ${NAMESPACE_DEV} || echo "namespace ${NAMESPACE_DEV} exists"
                    kubectl apply -f ${CONFIG_MAP_FILE} --namespace ${NAMESPACE_DEV}
                    kubectl apply -f deploy.yml  --namespace ${NAMESPACE_DEV}
                    kubectl apply -f service.yml --namespace ${NAMESPACE_DEV}
                    kubectl apply -f ingress.yml --namespace ${NAMESPACE_DEV}

                    kubectl get pods --namespace ${NAMESPACE_DEV}
                    kubectl get svc --namespace ${NAMESPACE_DEV}
                    kubectl -n ${NAMESPACE_DEV} get deploy
                    kubectl -n ${NAMESPACE_DEV} get ingress
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

