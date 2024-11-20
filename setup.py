from setuptools import setup, find_packages
import os

setup(
    name='quiz_app',
    version='1.3',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    py_modules=['sample_questions_pmle.main'],
    install_requires=[
        'PyMuPDF',
    ],
    entry_points={
        'console_scripts': [
            'quiz_app = sample_questions_pmle.main:extract_questions_from_pdf',
        ],
    },
    author='Tu Nombre',
    author_email='santiago.arranz.sanz@gmail.com',
    description='Aplicación interactiva de cuestionarios basada en Tkinter',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/santhiperbolico/sample_questions_pmle',  # Cambia esto si es necesario
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)