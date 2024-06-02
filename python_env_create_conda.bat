@REM 1. CD To the path of the scripts
SET mypath=%~dp0
cd %mypath:~0,-1%
%mypath:~0,2%

@REM 2. Set environment name, python version, requirements path and activate.bat path
set env_name=python_analysis
set python_version=3.10
set path_requirements=requirements.txt
set path_activate=C:\Users\i9h002\anaconda3\Scripts\activate.bat

@REM 3. Actviate conda, and create environment
call %path_activate%
call conda config --set ssl_verify no
echo y|call conda create --name %env_name% python=%python_version%
call conda activate %env_name%
call conda config --add channels conda-forge
call conda config --set ssl_verify no
rem echo y|call conda install jupyter notebook==4.6.0 # Fail install
rem echo y|call conda install -c conda-forge jupyter_contrib_nbextensions # Fail install
echo y|call conda install jupyter_nbextensions_configurator
echo y|call conda install jupyter_contrib_nbextensions
echo y|call conda install -c conda-forge jupytext 
rem echo y|call jupyter contrib nbextension install --user # Fail install

echo y|call pip install -r %path_requirements%

pause

