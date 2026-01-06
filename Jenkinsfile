pipeline {
    agent any
    
    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY') 
        CYNWUMOYE_KEY         = credentials('CynWumOye_CYO_KEY')
        AWS_ECR_REGION        = 'eu-west-1' 
        AWS_ACCOUNT_ENV       = "647743454395"   
        CONFIGMAP_BASE_S3     = "techbleat-terraform-state-cynwumoye"
        REPOSITORY_NAME       = "p_fruits-veg-market"  
        PROJECT_NAME          = "fruits-veg-market-app"      
        CONFIG_MAP_FILE       = "configmap-fruits-veg_market.yml"  
        ECR_REPO              = "${AWS_ACCOUNT_ENV}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${REPOSITORY_NAME}"
        NAMESPACE_DEV         = "cynwumoye"
    } 
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'STAGE', 'PROD'],
            description: 'Select the environment to deploy to'
        )
    }
    
    stages {
        stage("Build & Tag Docker Image for Python FastAPI App") {
            steps {
                script {
                    // Building Docker Image for ${REPOSITORY_NAME}
                    sh "echo building Docker image for ${REPOSITORY_NAME}"
                    sh "docker build -t ${REPOSITORY_NAME}:${BUILD_NUMBER} ."

                    // Tag Docker Image for ${REPOSITORY_NAME}
                    sh "echo tagging Docker image for ${REPOSITORY_NAME}:${BUILD_NUMBER}"
                    sh "docker tag ${REPOSITORY_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${BUILD_NUMBER}"
                }
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
                    aws ecr get-login-password --region ${AWS_ECR_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}

                    echo 'Pushing ${REPOSITORY_NAME} Docker Image to ECR'
                    docker push ${ECR_REPO}:${BUILD_NUMBER}
                """
            }
        }
        
        stage('Download ConfigMap from S3 and Update Deploy file') {
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
                    aws s3 cp s3://${CONFIGMAP_BASE_S3}/${PROJECT_NAME}/config/${env.BRANCH_NAME}/${CONFIG_MAP_FILE} .
                    
                    aws s3 cp s3://${CONFIGMAP_BASE_S3}/${PROJECT_NAME}/cynwumoye-app-manifest/${env.BRANCH_NAME}/deploy.yml . || exit 1
                    aws s3 cp s3://${CONFIGMAP_BASE_S3}/${PROJECT_NAME}/cynwumoye-app-manifest/${env.BRANCH_NAME}/service.yml .
                    aws s3 cp s3://${CONFIGMAP_BASE_S3}/${PROJECT_NAME}/cynwumoye-app-manifest/${env.BRANCH_NAME}/ingress.yml .
                    
                    # 2. Perform replacements
                    sed -i "s/VERSION_AUTO_REPLACE/${env.BUILD_NUMBER}/g" deploy.yml
                    sed -i "s|var_img|${ECR_REPO}|g" deploy.yml

                    # 3. Debugging
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
        
        stage('Deploy Image to EKS dev cluster') {
            when {
                anyOf {
                    branch "dev"
                }
            }
            steps {
                sh """ 
                    aws eks update-kubeconfig --name CynWumOye_CYO-cluster --region eu-west-1
                    
                    kubectl get pods --namespace ${NAMESPACE_DEV}

                    kubectl create namespace cynwumoye --dry-run=client -o yaml | kubectl apply -f -
                    sed -i 's/fruits-veg_market/fruits-veg-market/g' *.yml

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

        stage('Deploy Frontend Application') {
            when {
                anyOf {
                    branch "dev"
                }
            }
            steps {
                //withCredentials([file(credentialsId: 'CynWumOye_CYO_KEY', variable: 'CYNWUMOYE_KEY')]) {
                withCredentials([sshUserPrivateKey(credentialsId: 'CynWumOye_CYO_KEY', keyFileVariable: 'CYNWUMOYE_KEY')]) {
        sh """
            ssh -o StrictHostKeyChecking=no -i $CYNWUMOYE_KEY ec2-user@3.254.104.145 <<'EOF'
                set -e
                sudo yum install -y git
                rm -rf fruits-veg_market
                git clone -b dev https://github.com/olaoyeleye/fruits-veg_market.git 
                cd fruits-veg_market/frontend
                sed -i 's|http://localhost:8000/api/products|https://cynwumoye.duckdns.org/v1/api/products|g' index.html
                sudo cp index.html /usr/share/nginx/html/index.html
                sudo systemctl restart nginx

                
    EOF
        
                 """
                }
            }
        }
        
        stage("Deployment Approval") {
            when {
                anyOf {
                    branch "prod"
                }
            }
            steps {
                script {
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
            deleteDir()
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
}