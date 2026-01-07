i want to build a project for building images from scratch for deploying code. I want to build final image by having some base opertaing system OS's like Ubuntu, Redhat, Alpine. Also, we need pcakages for languages like python, java etc. Next, we need are components that our images require like it could be agents for proemetheus, pass vault, puppet agent. Nect, we would scan the images by using some security scanner to check vulnerabilties in image. And the last step would be to upload the image to my personal/local docker hub kind of repository. 

so our goal is to pre-develop images (container images) which has various combinations of: OS + language + components- similar to product like Chainguard.
so when someone has to develop image using their code, they just use one of our pre-built images from our local repo and add their code in it and are good to go.
we can also add the image step into CICD pipeline so that when user uploads github code in Jenkins or some CICD product, automatically his code goes through pipeline of building image using our local repo and deploying the image into containers. pipeline doesnt have to go through individual image creation steps (i.e. combining OS+ language +components+Security scan).



Step0: I want you to download 3 images from public docker hub. Ubuntu OS, Redhat os and Alpine OS.
images should be light, less than 200MB.
