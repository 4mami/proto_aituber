FROM pytorch/pytorch:2.12.0-cuda13.2-cudnn9-runtime

ARG USERID
ARG GROUPID
ARG USERNAME

RUN apt update && apt install -y git

RUN groupadd -g ${GROUPID} ${USERNAME} \
  && useradd -u ${USERID} -g ${GROUPID} -s /bin/bash -m ${USERNAME}

USER ${USERID}

WORKDIR /work

COPY ../work/requirements.txt ./

RUN pip install --upgrade pip --break-system-packages
# RUN pip install -r requirements.txt

CMD ["/bin/bash"]
