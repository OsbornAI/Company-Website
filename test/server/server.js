import express from 'express';
import fs from 'fs';
import path from 'path';

import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { StaticRouter } from'react-router-dom';

import App from '../src/App';

const app = express();
const PORT = 8000;

app.use('^/$', (req, res, next) => {
    fs.readFile(path.resolve('./build/index.html'), 'utf-8', (err, data) => {
        if (err) {
            console.log(err);
            return res.status(500).send('Server encountered an error!');
        }
        return res.send(data.replace(
            '<div id="root"></div>',
            `<div id="root">${ReactDOMServer.renderToString(
            <StaticRouter>
                <App />
            </StaticRouter>
            )}</div>`
        ));
    });
});

app.use(express.static(path.resolve(__dirname, '..', 'build')));

app.listen(PORT, () => {console.log("Server running")});