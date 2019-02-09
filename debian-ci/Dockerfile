FROM debian:stretch
ENV COMPOSE_VERSION 1.22.0
ENV NPM_VERSION 10

ARG DEBIAN_FRONTEND="noninteractive"

# Get certificate material in
COPY ca-certificates /usr/local/share/ca-certificates/

# Get Python and Docker
RUN apt-get update -qy \
    && apt-get install -qy \
      apt-transport-https \
      bash-completion \
      ca-certificates \
      curl \
      git \
      gnupg2 \
      groff-base \
      httpie \
      jq \
      less \
      python \
      python-pip \
      python3 \
      python3-nose \
      python3-pip \
      software-properties-common \
      unzip \
      wget \
      zip \
    && update-ca-certificates \
    && groupadd -g 155 docker \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && add-apt-repository \
         "deb [arch=amd64] https://download.docker.com/linux/debian \
         $(lsb_release -cs) \
         stable" \
    && apt-get update -qy \
    && apt-get -qy install --no-install-recommends docker-ce \
	  && curl -o /usr/local/bin/docker-compose -L \
		  "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-Linux-x86_64" \
	  && chmod +x /usr/local/bin/docker-compose

# Get node and npm
RUN curl -sL https://deb.nodesource.com/setup_${NPM_VERSION}.x | bash - \
    && apt-get -qy install --no-install-recommends nodejs \
    && useradd -ms /bin/bash user \
    && adduser user docker

# Get AWS CLI
RUN curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "/tmp/awscli-bundle.zip" \
    && unzip -d /tmp /tmp/awscli-bundle.zip \
    && /tmp/awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws \
    && /tmp/awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws_completer \
    && rm -rf /tmp/awscli-bundle /tmp/awscli-bundle.zip /var/lib/apt/lists/* \
    && ln -s /usr/local/aws/bin/aws_bash_completer /etc/bash_completion.d/aws_bash_completer

# Get ASK
USER user
RUN cd /home/user \
    && npm init -y \
    && npm install ask-cli@1.4

ENV PATH="/home/user/node_modules/.bin:${PATH}"
