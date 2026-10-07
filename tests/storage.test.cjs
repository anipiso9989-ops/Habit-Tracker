const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync(require('node:path').join(__dirname, '../index.html'), 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
function app({stored = null, fail = false} = {}) {
    const elements = new Map();
    const node = () => ({textContent:'', value:'', files:[], classList:{toggle(){}}, addEventListener(){}, append(){}, replaceChildren(){}, querySelector(){return node();}, click(){}, remove(){}});
    const context = vm.createContext({Date, Set, Number, JSON, Blob, URL, confirm:()=>true, prompt:()=>null, setTimeout:()=>0, setInterval:()=>0,
        document:{hidden:false, body:node(), addEventListener(){}, createElement:node, getElementById(id){if(!elements.has(id))elements.set(id,node());return elements.get(id);}},
        localStorage:{getItem(){if(fail)throw Error('blocked');return stored;},setItem(key,value){if(fail)throw Error('quota');stored=value;}}});
    vm.runInContext(script,context);
    return {run:code=>vm.runInContext(code,context), saved:()=>stored, elements};
}
const habit = {id:1,name:'Read',created:'2026-10-06',completions:['2026-10-06']};
test('original JSON round trip and invalid imports',()=>{
    const a=app();
    assert.equal(a.run(`JSON.stringify(validateHabits(${JSON.stringify([habit])}))`),JSON.stringify([habit]));
    for(const data of [{},[{...habit,id:'1'}],[habit,habit],[{...habit,name:' '}],[{...habit,created:'2026-02-30'}],[{...habit,completions:['2026-10-06','2026-10-06']}],[{...habit,completions:['junk']}]] ) {
        assert.throws(()=>a.run(`validateHabits(${JSON.stringify(data)})`));
    }
    assert.equal(a.run('JSON.stringify(validateHabits([]))'),'[]');
});
test('mutations survive reload and export matches old file schema',async()=>{
    const a=app();a.elements.get('habit-name').value='Read';a.run('addHabit()');
    const b=app({stored:a.saved()});assert.equal(b.run('habits[0].name'),'Read');
    b.run('exportFile()');assert.equal(b.run('backupJSON'),b.run('JSON.stringify(habits)'));
    assert.equal(b.run('JSON.stringify(validateHabits(JSON.parse(backupJSON)))'),b.run('JSON.stringify(habits)'));
    a.elements.get('habit-name').value='Second';a.run('addHabit()');assert.equal(a.run('habits[1].id'),2);
});
test('storage unavailable still permits in-memory changes and export',()=>{
    const a=app({fail:true});a.elements.get('habit-name').value='Read';a.run('addHabit(); exportFile()');
    assert.equal(a.run('habits.length'),1);assert.equal(a.run('storageAvailable'),false);
});
test('corrupt storage is protected and valid import recovers it',async()=>{
    const a=app({stored:'broken'});a.elements.get('habit-name').value='Read';a.run('addHabit()');assert.equal(a.saved(),'broken');
    a.run(`globalThis.event = {target:{files:[{text:async()=>${JSON.stringify(JSON.stringify([habit]))}}],value:'file'}}`);
    await a.run('importFile(event)');assert.equal(a.run('loadBlocked'),false);assert.equal(a.run('habits[0].name'),'Read');
});
test('invalid import preserves current data',async()=>{
    const a=app({stored:JSON.stringify({habits:[habit],backupJSON:null})});const before=a.saved();
    a.run(`globalThis.event = {target:{files:[{text:async()=>'[{"id":1}]'}],value:'file'}}`);
    await a.run('importFile(event)');assert.equal(a.saved(),before);assert.equal(a.run('habits.length'),1);
});
test('streaks handle yesterday, gaps, leap days, year rollover, and DST',()=>{
    const a=app();
    for(const [days,now,expected] of [
        [['2026-10-05','2026-10-06'],'2026-10-06',2],
        [['2026-10-05'],'2026-10-06',1],
        [['2026-10-04'],'2026-10-06',0],
        [['2024-02-28','2024-02-29','2024-03-01'],'2024-03-01',3],
        [['2025-12-31','2026-01-01'],'2026-01-01',2],
        [['2026-03-07','2026-03-08','2026-03-09'],'2026-03-09',3]]) {
        assert.equal(a.run(`calculateStreak({completions:${JSON.stringify(days)}},new Date('${now}T12:00:00'))`),expected);
    }
});
