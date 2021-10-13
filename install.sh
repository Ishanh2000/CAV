# AUM SHREEGANESHAAYA NAMAH||

PY=""
CAV="cav" # virtual env name

if command -v python3 &> /dev/null
then
  PY="python3"
elif command -v python &> /dev/null
then
  PY="python"
else
  echo "python could not be found. Please install python yourself."
  exit
fi

echo "Checking virtualenv installed virtualenv"
$PY -m pip install virtualenv

echo "Creating virtualenv $CAV"
$PY -m venv $CAV
source $CAV/bin/activate
echo "Installing numpy, flask, flask-cors, redis"
$PY -m pip install numpy 
$PY -m pip install flask
$PY -m pip install flask-cors
$PY -m pip install redis

echo
echo -e "\033[33;1mInsatllation successful!\033[m"
echo -e "Use \033[32;1msource $CAV/bin/activate\033[m to activate and run \033[32;1m$PY main.py\033[m"
echo -e "Use \033[32;1mdeactivate\033[m to deactivate"


