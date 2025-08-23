# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

OAuth = os.getenv('OAuth')
