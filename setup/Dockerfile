ARG BASE_IMG

FROM $BASE_IMG

RUN yes | pip3 install virl2_client pytest requests

ADD /nso_test_restconf /nso_test_restconf
RUN cd /nso_test_restconf; pip3 install .
