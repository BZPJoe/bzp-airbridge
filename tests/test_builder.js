const assert=require('node:assert/strict');
const {validateRemoteBackup}=require('../firmware/ui/builder.js');
const blank=()=>({schema:2,profile:'433.937MHz ASK/OOK',remotes:['Test','','',''],buttons:Array.from({length:8},(_,slot)=>({slot,name:'',remote:0,icon:0,order:slot,active:false,pulses:[]}))});
let data=blank();validateRemoteBackup(data);
data.buttons[0].active=true;data.buttons[0].name='<img src=x onerror=alert(1)>';
data.buttons[0].pulses=Array.from({length:16},(_,i)=>i%2?-400:400);validateRemoteBackup(data);
for(const mutate of [d=>d.schema=99,d=>d.remotes[0]='',d=>d.buttons[0].slot=7,d=>d.buttons[0].remote=-1,d=>d.buttons[0].icon=8,d=>d.buttons[0].order=8,d=>d.buttons[0].pulses[1]=400,d=>d.buttons[0].pulses[0]=2**32,d=>d.buttons[0].name='\0',d=>d.buttons[0].pulses=Array(257).fill(400),d=>d.buttons[0].name='😀'.repeat(9)]){
  const copy=structuredClone(data);mutate(copy);assert.throws(()=>validateRemoteBackup(copy));
}
console.log('Backup schema, bounds, hostile labels, and pulse validation passed.');
