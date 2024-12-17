const encryptAES = require('./encryptAES');

const password = process.argv[2];
const salt = process.argv[3];

const encryptedPassword = encryptAES(password, salt);
console.log(encryptedPassword);