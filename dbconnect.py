from flask import Flask,flash
import pymysql


def connection():
    conn = pymysql.connect(host="localhost",
                           user = "root",
                           passwd = "Bharat2018*",
                           db = "pythonprogramming")
    c = conn.cursor()
    return c, conn