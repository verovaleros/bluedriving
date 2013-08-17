#!/bin/bash
echo -n "$1 | "
wget -qO- "http://www.coffer.com/mac_find/?string=$1"|grep -i "class=\"Table2\"><a"|awk -F"q=" '{print $2}'|awk -F\" '{print $1}'|uniq
