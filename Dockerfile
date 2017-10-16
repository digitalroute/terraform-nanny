FROM hashicorp/terraform:light

# Install python3
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    rm -r /root/.cache

COPY terraform-nanny.py /usr/bin/terraform-nanny
RUN chmod +x /usr/bin/terraform-nanny
