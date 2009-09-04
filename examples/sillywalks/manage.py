#!/usr/bin/env python
import sys
import os

import settings
from django.core import management

if __name__ == "__main__":
    management.execute_manager(settings)
