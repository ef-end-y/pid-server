#! -*- coding: utf-8 -*-
import os
import logging.config

PROJECT_PATH = os.path.dirname(__file__)

PID_ANALYZER_PATH = os.path.join(PROJECT_PATH, 'PID-Analyzer/PID-Analyzer.py')
BLACKBOX_DECODER_PATH = os.path.join(PROJECT_PATH, 'blackbox-tools/obj/blackbox_decode')

NOISE_BOUNDS = '[[1.0,10.1],[1.0,100.0],[1.0,100.0],[0.0,4.0]]'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': PROJECT_PATH + '/error.log'
        },
    },
    'loggers': {
        'aiohttp.server': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING)

PAGES = {
    'css': '''
html, body {
    height: 100%;
    min-height: 100%;
    width: 100%;
    font-size: 18pt;
    font-family: Tahoma, sans-serif;
    color: #304050;
    background-color: #ffffff;
}
input[type='submit'] {
    margin-top: 20pt;
    display: block;
    font-size: 18pt;
    padding: 5pt 15pt;
    border-style: outset;
    color: #ffffff;
    background-color: #304050;
    border: 1px solid #000000;
}
input[type='text'] {
    width: 100%;
    margin-top: 20pt;
    font-size: 20pt;
    padding: 2pt;
    color: #304050;
    background-color: #e0e0e0;
    border: 1px solid #304050;
}
.center-container {
    position: relative;
    height: 100%;
}
.absolute-center {
    width: 50%;
    height: 50%;
    overflow: auto;
    margin: auto;
    position: absolute;
    top: 0; left: 0; bottom: 0; right: 0;
}
.error {
    color: #ff0000;
}
.log {
    font-size: 50%;
    margin-top: 10pt;
    white-space: pre;
    overflow: scroll;
}
.add_info {
    margin-top: 45pt;
    font-size: 70%;
}
    ''',

    'html': '''
        <html>
        <head>
            <title>Online PID-analyzer</title>
            <meta http-equiv='Cache-Control' content='no-cache'>
            <meta http-equiv='Pragma' content='no-cache'>
            <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
            <meta name='copyright' content='max.begemot'>
            <style>{css}</style>
        </head>
        <body>
            {body}
        </body>
        </html>
        ''',

    'error': '''
                <div class='error'>{error}</div>
            ''',

    'index': '''
            <div class='center-container'>
                <div class='absolute-center'>
                    {error}
                    <h3>Online PID-analyzer</h3>
                    <form action='{url}' enctype='multipart/form-data' method='post'>
                        <label for='bbl_file'>BBL log file to analyse:</label>
                        <input id='bbl_file' type='file' name='bbl_file'>
                        <br><br>
                        <label for='noise_bounds'>Bounds of plots in noise analysis:</label>
                        <input id='noise_bounds' type='text' name='noise_bounds' value={noise_bounds}>
                        <input type='submit' value='Analyze'>
                    </form>
                    <div class='add_info'>
                        Additional info:
                        <ul>
                            <li><a href='https://github.com/Plasmatree/PID-Analyzer'>PID-Analyzer</a>
                        </ul>
                    </div>
                </div>
            </div>
            ''',

    'result': '''
            <script>
                setTimeout(function() {{
                   window.location.href = '{result_url}?job_id={job_id}&step={step}';
                }}, 3000);
            </script>
            <div class='center-container'>
                <div class='absolute-center'>
                    {result}
                    <p>{files} pictures ready<p>
                    <div class='log'>{log}</div>
                </div>
            </div>
        ''',

    'result_ok': '''
            <p>Yes! <a href='{index_url}'>Try again</a></p>
            {files}
            <p>Log:</p>
            <div class='log'>{log}</div>
    ''',
}
