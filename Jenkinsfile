pipeline {
    agent { label 'dev-test' }
    parameters {
        string(name: 'AWS_BUCKET', defaultValue: 'niis-xrdsst-development', description: 'Bucket name for downloading configuration anchor')
    }
    options {
        timeout(time: 90, unit: 'MINUTES')
    }
    stages {
        stage('checkout X-Road Security Server Toolkit') {
            steps {
                echo "Checking out X-Road Security Server Toolkit..."
                checkout(changelog: false, poll: false, scm: [
                        $class                           : 'GitSCM',
                        branches                         : [[name: 'master']],
                        doGenerateSubmoduleConfigurations: false,
                        extensions                       : [[$class: 'CleanCheckout']],
                        gitTool                          : 'Default',
                        submoduleCfg                     : [],
                        userRemoteConfigs                : [[url: 'https://github.com/nordic-institute/X-Road-Security-Server-toolkit.git']]
                ])
            }
        }
        stage('Download configuration anchor from S3') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'AWS', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY'), file(credentialsId: "jenkins-gpg-key", variable: 'KEY')]) {
                    withAWS(region: params.AWS_REGION, credentials: params.AWS_CREDENTIALS) {
                        s3Download(pathStyleAccessEnabled: true, file:'/tmp/toolkit/configuration_anchor.xml', bucket: params.AWS_BUCKET, path:'configuration_anchor.xml', force:true)
                    }
                }
            }
        }
        stage('Install X-Road Security Server Toolkit') {
            steps {
                script {
                    sh '''
                        echo $WORKSPACE
                        mv tests/resources/configuration-anchor.xml tests/resources/configuration-anchor2.xml
                        mv /tmp/toolkit/configuration_anchor.xml tests/resources/configuration-anchor.xml
                        python3 -m venv env
                        echo $WORKSPACE
                        . env/bin/activate
                        pip install -r requirements-dev.txt
                        python3 setup.py develop
                        '''
                    }
            }
        }
        stage('Run integration tests for X-Road Security Server Toolkit') {
            steps {
                script {
                    sh '''
                        . env/bin/activate
                        make test-all
                       '''
                    }
            }
        }
    }
}
