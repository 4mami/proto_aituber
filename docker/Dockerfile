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

# 名前付きボリューム(models)のマウント先をユーザー権限で先に作成しておく。
# 空ボリュームはイメージ側マウント先の所有権を引き継いで初期化されるため、
# これが無いと Docker が root 所有で初期化し HF のモデルDLが書き込めない。
RUN mkdir -p /home/${USERNAME}/.cache/huggingface/hub

WORKDIR /work

RUN curl -fsSL https://claude.ai/install.sh | bash

COPY ../src/requirements.txt ./

RUN pip install --upgrade pip --break-system-packages
RUN pip install -r requirements.txt --break-system-packages

# bitsandbytes 0.49.2 は CUDA 13.2 向けバイナリを含まないため cuda130 で代用
RUN python -c "\
import os, bitsandbytes; \
d = os.path.dirname(bitsandbytes.__file__); \
src = os.path.join(d, 'libbitsandbytes_cuda130.so'); \
dst = os.path.join(d, 'libbitsandbytes_cuda132.so'); \
os.symlink(src, dst) if os.path.exists(src) and not os.path.exists(dst) else None"

CMD ["/bin/bash"]
