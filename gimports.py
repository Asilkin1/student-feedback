# Flask barebones
from flask import Flask, render_template, request, redirect, url_for, session, app, abort, flash, make_response, Response, render_template_string
from flask_session.__init__ import Session as flaskGlobalSession

from models import create_post, get_posts, delete_posts, create_class
from datetime import date, datetime, timedelta  # get date and time
from sqlalchemy.orm import sessionmaker  # Making Sessions and login
from sqlalchemy import insert, delete, event
from CreateUserDatabase import *    # Table for Users
import time  # date and time
import os  # filepath
# Encryption stuff
from Crypto.Cipher import AES
from base64 import b64encode
import Padding
import binascii
import hashlib



import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3 as sql

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io