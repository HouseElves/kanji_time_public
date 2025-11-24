:orphan:

Installing
==========

This chapter mirrors the installation guide available on the Kanji Time GitHub `landing page <https://github.com/HouseElves/kanji_time_public>`__.

There are two ways to get Kanji Time.

    #) You can install & run the latest released Kanji Time package, **or**,
    #) You can build, install, and run Kanji Time from the latest source code.

Install the latest Kanji Time release
-------------------------------------

Kanji Time runs on Python 3.11.0 or later.

The installation instructions below have been verified on **Windows 10** (Build 19045.5965), **Ubuntu 22.04.5 LTS**, and **macOS 15.5 "Sequoia"**.  

These steps will install Kanji Time using the latest development wheel from GitHub.  

Kanji Time will be *isolated inside its own virtual environment using `venv`* so it does not interfere with your existing Python applications.

    - If you're unfamiliar with virtual environments and would like to learn more, the Real Python site has an excellent
      `primer <https://realpython.com/python-virtual-environments-a-primer/>`__.

    - If you already use virtual environments, feel free to substitute appropriate commands for your preferred tool (such as `pyenv` or `virtualenv`).
      Kanji Time is agnostic to how the environment is managed.

From the command line, create (or navigate to) a parent directory for Kanji Time (e.g., `PythonApps`).
Kanji Time will be installed into a directory named `.kanji_time` under this parent.

Now run the appropriate commands for your operating system.

On **Windows**
~~~~~~~~~~~~~~

.. code-block:: batch
   :caption: Installing Kanji Time on Windows

        python3 -m venv .kanji_time
        .kanji_time\Scripts\activate
        pip3 install https://github.com/HouseElves/kanji_time_public/releases/download/v0.1.2-alpha-20251123/kanji_time-0.1.1a20250606-py3-none-any.whl

On **macOS** or **Linux**
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   :caption: Installing Kanji Time on macOS or Linux

        python3 -m venv .kanji_time
        source .kanji_time/bin/activate
        pip3 install https://github.com/HouseElves/kanji_time_public/releases/download/v0.1.2-alpha-20251123/kanji_time-0.1.1a20250606-py3-none-any.whl

----

Build Kanji Time from source code
---------------------------------

The below command line snippets will clone the Kanji Time github `repository <https://github.com/HouseElves/kanji_time_public>`__
, deploy all the required Python packages into a virtual environment, build a local installation wheel, then install it.  

Before you start, create (or navigate to) a parent directory for Kanji Time (e.g., `PythonCode`).
Now run one of the below snippets appropriate to your operating system.

On **Windows**
~~~~~~~~~~~~~~

.. code-block:: batch
   :caption: Building Kanji Time from source code on Windows

        rem Get the source code
        git clone https://github.com/HouseElves/kanji_time_public.git
        cd kanji_time_public
        rem Make a virtual environment
        python3 -m venv .kanji_time
        .kanji_time\Scripts\activate
        rem Build
        pip3 install -r requirements.txt
        pip3 install --upgrade build
        python3 -m build
        rem Install
        pip3 install -e .

On **macOS** or **Linux**
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   :caption: Building Kanji Time from source code on macOS or Linux

        # Get the source code
        git clone https://github.com/HouseElves/kanji_time_public.git
        cd kanji_time_public
        # Make a virtual environment
        python3 -m venv .kanji_time
        source .kanji_time/bin/activate
        # Build
        pip3 install -r requirements.txt
        pip3 install --upgrade build
        python3 -m build
        # Install
        pip3 install -e .

----

Command Line Quick Start
------------------------

Once installed, you can generate sample kanji reports from the command line.
The below command will run Kanji Time to produce dictionary information and stroke practice sheets for the characters `現`, `生`, and `鳥`.

.. code-block:: bash

        python3 -m kanji_time 現 生 鳥 --report=kanji_summary --report=practice_sheet

After a moment or two, you will see output similar to this:

.. code-block::

    Loading extra kanji information...
    Loading the kanji dictionary...
    Beginning kanji_summary.
    Processing 現...on page...1...done! PDF result in 96_現_summary.pdf
    Processing 生...on page...1...2...3...done! PDF result in 100_生_summary.pdf
    Processing 鳥...on page...1...done! PDF result in 196_鳥_summary.pdf
    kanji_summary complete.
    Finished.  Execution log in kanji_summary.log
    Beginning practice_sheet.
    Processing 現...on page...1...done! PDF result in 現_practice.pdf
    Processing 生...on page...1...done! PDF result in 生_practice.pdf
    Processing 鳥...on page...1...done! PDF result in 鳥_practice.pdf
    practice_sheet complete.
    Finished.  Execution log in practice_sheet.log

Each of the processed kanji will have its own summary and practice sheet PDF in the current directory.

