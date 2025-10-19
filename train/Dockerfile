FROM ubuntu:22.04

# 環境変数の設定
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
    wget \
    automake \
    ca-certificates \
    g++ \
    libtool \
    libleptonica-dev \
    make \
    pkg-config \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    zlib1g-dev \
    libicu-dev \
    libpango1.0-dev \
    libcairo2-dev \
    python3 \
    python3-pip \
    imagemagick \
    bc \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-ipaexfont \
    fonts-takao-gothic \
    fonts-takao-mincho \
    && rm -rf /var/lib/apt/lists/*

# Tesseractのビルドとインストール
WORKDIR /tmp
RUN git clone --depth 1 --branch 5.3.3 https://github.com/tesseract-ocr/tesseract.git && \
    cd tesseract && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    make training && \
    make training-install && \
    ldconfig && \
    cd .. && \
    rm -rf tesseract

# Tesseractトレーニングツールのインストール
RUN git clone --depth 1 https://github.com/tesseract-ocr/tesstrain.git /opt/tesstrain

# 作業ディレクトリの設定
WORKDIR /workspace

# Pythonパッケージのインストール
RUN pip3 install pillow

CMD ["/bin/bash"]
