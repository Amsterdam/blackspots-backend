#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}

node {
    stage("Checkout") {
        checkout scm
    }


    stage('Test') {
        tryStep "Test", {
            sh "import/deploy/test/test.sh"
        }
    }


    stage("Build develop image") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/blackspots-import:${env.BUILD_NUMBER}", "import")
            image.push()
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {
    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("build.datapunt.amsterdam.nl:5000/datapunt/blackspots-import:${env.BUILD_NUMBER}")
                image.pull()
                image.push("acceptance")
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'Tellus is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                def image = docker.image("build.datapunt.amsterdam.nl:5000/datapunt/blackspots-import:${env.BUILD_NUMBER}")
                image.pull()
                image.push("production")
                image.push("latest")
            }
        }
    }
}
