// Load the filesystem module
const fs = require('fs');

fs.readFile('javascript/myfile.txt', 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading file: ' + data);
        return;
    }

    console.log('File content: ' + data);

});


console.log('Reading file... (this runs first!)'); 