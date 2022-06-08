const fs = require('fs');

module.exports = {
  setFormBody,
};

function setFormBody(requestParams, context, ee, next) {
  var file = fs.createReadStream(__dirname + '\\receipt4.jpg');
//   console.log(file.path);
  const formData = {
    file: file,
  };
  requestParams.formData = Object.assign({}, formData);
//   console.log(requestParams);
  return next();
}
