#!/bin/bash
#############################################
## Supported environment:
##   - macOs (Darwin Kernel)
##   - Ubuntu (Linux Kernel)
#############################################

_UNAME_OUT="$(uname -s)"
_HOME_PATH="${HOME-~}"
_CONDA_HOME="${1-${_HOME_PATH}/conda}"

# Install conda environment
echo "Start to install conda, the current OS Kernel is: ${_UNAME_OUT}, the conda installation path is: ${_CONDA_HOME}, the environment variable address is: ${_HOME_PATH}/.bashrc"
case "${_UNAME_OUT}" in
Linux*) _MACHINE=Linux ;;
Darwin*) _MACHINE=Mac ;;
CYGWIN*) _MACHINE=Cygwin ;;
MINGW*) _MACHINE=MinGw ;;
*) _MACHINE="UNKNOWN:${_UNAME_OUT}" ;;
esac
echo "${_MACHINE}"
if [ ! -x "$(command -v conda)" ]; then
  if [ -x "${_CONDA_HOME}"/etc/profile.d/conda.sh ]; then
    . "${_CONDA_HOME}"/etc/profile.d/conda.sh
    if [ ! -x "$(command -v conda)" ]; then
      echo "Error: installation failed! The ${_CONDA_HOME} directory already exists, but command of conda cannot be used. Please try to repair or delete it and try again."
      exit 1
    fi
  fi
  _MINICONDA3_DOWNLOAD_URL=""
  if [ "${_MACHINE}" = "Mac" ]; then
    _MINICONDA3_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    # miniconda requires bzip2
    if [ ! -x "$(command -v bzip2)" ]; then
      if [ ! -x "$(command -v brew)" ]; then
        echo "" &&
          echo "Error: Please install homebrew to your macOs first. You can run the following commands:" &&
          echo "" &&
          echo '      /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"' &&
          echo "" &&
          exit 1
      fi
      brew install bzip2
    fi
  elif [ "${_MACHINE}" = "Linux" ]; then
    _MINICONDA3_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    # miniconda requires bzip2
    if [ ! -x "$(command -v bzip2)" ]; then
      apt-get update
      apt-get install bzip2
    fi
  else
    echo "Error: Windows  is not supported yet!"
    exit 0
  fi
  (wget --quiet ${_MINICONDA3_DOWNLOAD_URL} -O "$_HOME_PATH"/miniconda.sh &&
    /bin/bash "$_HOME_PATH"/miniconda.sh -b -p "${_CONDA_HOME}" &&
    rm "$_HOME_PATH"/miniconda.sh &&
    "${_CONDA_HOME}"/bin/conda clean -tipsy &&
    ln -s "${_CONDA_HOME}"/etc/profile.d/conda.sh /etc/profile.d/conda.sh &&
    _CONDA_ENV="\n# conda environment\n. ${_CONDA_HOME}/etc/profile.d/conda.sh\n. ${_CONDA_HOME}/bin/activate\nexport PATH=${_CONDA_HOME}/bin:"'$PATH' &&
    echo "$_CONDA_ENV" >>"$_HOME_PATH"/.bashrc &&
    . "$_HOME_PATH"/.bashrc &&
    echo "Conda initialization is complete!") ||
    (echo "Error: installation failed, please check the environment!" && exit 1)
else
  if [ ! -d "${_CONDA_HOME}" ];then
    if conda info -e | grep -q 'base';then
      _CONDA_PREFIX="$(conda env list | stdbuf -oL grep '^base' | head -n1)"
      _CONDA_HOME="$(echo "${_CONDA_PREFIX}" | awk -F '[ ]+' '{print $2}')"
      if echo "${_CONDA_PREFIX}" | grep -q -F '*';then
        _CONDA_HOME="$(echo "${_CONDA_PREFIX}" | awk -F '[ ]+' '{print $3}')"
      fi
    else
      echo "Error: can not find any path of conda!" && exit 1
    fi
    echo "Conda HOME is : ${_CONDA_HOME}"
  fi
  echo "Conda environment already exists, skipping..."
fi

# export PATH of activate
if [ ! -x "$(command -v activate)" ]; then
  _CONDA_ENV="\n# conda environment\n. ${_CONDA_HOME}/etc/profile.d/conda.sh\n. ${_CONDA_HOME}/bin/activate\nexport PATH=${_CONDA_HOME}/bin:"'$PATH'
  if whoami |grep -q 'root';then
    (echo "$_CONDA_ENV" >>/etc/profile &&
      . /etc/profile &&
      echo "export  PATH of activate success.") ||
      (echo "Error: can not export path of activate!")
  elif echo "$SHELL" |grep -q 'zsh'; then
    (echo "$_CONDA_ENV" >>"$_HOME_PATH"/.zshrc &&
      . "$_HOME_PATH"/.zshrc &&
      echo "export  PATH of activate success.") ||
      (echo "Error: can not export path of activate!")
  elif echo "$SHELL" |grep -q 'bash'; then
    (echo "$_CONDA_ENV" >>"$_HOME_PATH"/.bashrc &&
      . "$_HOME_PATH"/.bashrc &&
      echo "export  PATH of activate success.") ||
      (echo "Error: can not export path of activate!")
  fi
  export PATH=${_CONDA_HOME}/bin:'$PATH'
fi

# Add official channels
conda config --add channels conda-forge &&
  conda config --add channels defaults &&
  conda config --add channels r &&
  conda config --add channels bioconda

# Add tsinghua channels
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ &&
  conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ &&
  conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/ &&
  conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/ &&
  conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/ &&
  conda config --set show_channel_urls yes

# Check if it is installed
if conda env list | grep -q 'lib-core-py-367'; then
  echo "Conda env of lib-core-py-367 already exists, skipping..."
else
  echo "Start to create a conda environment with python version 3.6.7: lib-core-py-367..." &&
      conda create --name lib-core-py-367 python=3.6.7 &&
      echo "The conda environment is created."  
fi

source deactivate
source activate lib-core-py-367

(. "${_CONDA_HOME}"/bin/activate lib-core-py-367 &&
  echo "Start to install pip dependencies..." &&
  pip install --upgrade pip &&
  pip config set global.trusted-host mirrors.aliyun.com &&
  pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/ &&
  pip install --upgrade Cython pytest-runner aioredis==1.3.1 pyarrow==5.0.0 ray==1.3.0 \
    aiohttp psutil grpcio pandas xlsxwriter watchdog requests click uuid sfcli \
    pyjava vega_datasets plotly &&
  echo "Conda environment initialization is complete!") ||
  (echo "Error: installation failed, please check the environment!" && exit 1)
