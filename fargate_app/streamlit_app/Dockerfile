FROM public.ecr.aws/lambda/python:latest

WORKDIR /app
RUN yum update -y
RUN yum install -y sudo

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
COPY app.py ./app.py
RUN mkdir -p ./.streamlit
COPY .streamlit/config.toml ./.streamlit/config.toml

ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]