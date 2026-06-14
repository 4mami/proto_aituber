FROM pytorch/pytorch:2.12.0-cuda13.2-cudnn9-runtime

ARG USERID
ARG GROUPID
ARG USERNAME

RUN apt update && apt install -y git curl locales

RUN echo "ja_JP UTF-8" > /etc/locale.gen && locale-gen

ENV LANG=ja_JP.UTF-8

RUN groupadd -g ${GROUPID} ${USERNAME} \
  && useradd -u ${USERID} -g ${GROUPID} -s /bin/bash -m ${USERNAME}

USER ${USERID}

WORKDIR /work

RUN curl -fsSL https://claude.ai/install.sh | bash

COPY ../work/requirements.txt ./

RUN pip install --upgrade pip --break-system-packages
# RUN pip install -r requirements.txt

CMD ["/bin/bash"]
