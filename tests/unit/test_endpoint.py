from datetime import datetime
import sys
import unittest
from unittest import mock

import pytest

from tests.util.test_util import StatusTestData
from xrdsst.controllers.service import ServiceController
from xrdsst.models import Client, ConnectionType, ClientStatus, ServiceDescription, ServiceType, ServiceClient, ServiceClientType, Service
from xrdsst.main import XRDSSTTest
from xrdsst.rest.rest import ApiException