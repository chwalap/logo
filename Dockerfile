FROM python:latest

WORKDIR /usr/logo/

RUN pip install ply
COPY ./ /usr/logo/

ENTRYPOINT [ "python3" ]
CMD [ "logo.py", "demo.trtl" ]
