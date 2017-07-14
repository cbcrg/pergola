FROM pergola/pergola:paper_2

MAINTAINER Jose Espinosa-Carrasco <espinosacarrascoj@gmail.com>

# I need this to avoid the broken package list apt
RUN rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends git \
                                               libssl-dev \
                                               openssl \
                                               mysql-client-5.7 \
                                               mysql-client-core-5.7 \
                                               libmysqlclient-dev
                                            
# Compile and install kentUtils 
RUN cd /tmp && \
    git clone https://github.com/ENCODE-DCC/kentUtils.git && \
    cd kentUtils && \
    git checkout v302.1.0 && \
    make && \
    cp -rp bin/* /usr/local/bin && \
    cd .. && rm -rf kentUtils

# Compile and install bwtool
RUN git clone https://github.com/CRG-Barcelona/libbeato.git && \
    git clone https://github.com/CRG-Barcelona/bwtool.git && \
    cd libbeato/  &&  ./configure && \
    make && \
    sudo make install && \
    cd ../bwtool/  && ./configure && \
    make && \
    sudo make install
