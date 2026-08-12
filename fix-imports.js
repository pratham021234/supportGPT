const fs = require('fs');
const path = require('path');

const dir = 'src/lib/api';
const files = fs.readdirSync(dir);

files.forEach(file => {
  if (file.endsWith('.ts') && file !== 'api-client.ts') {
    const fullPath = path.join(dir, file);
    let content = fs.readFileSync(fullPath, 'utf8');
    if (content.includes("from './api-client'")) {
      content = content.replace(/from '\.\/api-client'/g, "from './client'");
      fs.writeFileSync(fullPath, content);
      console.log('Updated', file);
    }
  }
});

try {
  fs.unlinkSync('src/lib/api/api-client.ts');
} catch (e) {}

console.log('Done');
