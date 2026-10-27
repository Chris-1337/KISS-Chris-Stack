import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const workspaceDir='C:/Users/chris.sass/Documents/Codex/2026-09-22/c-users-chris-sass-downloads-ouroboros';
const buildDir=path.join(workspaceDir,'work/management-slide');
const skillDir='C:/Users/chris.sass/.codex/plugins/cache/openai-primary-runtime/presentations/26.1005.12141/skills/presentations';
const finalPath=path.join(workspaceDir,'outputs/KISS-Chris-Stack_Architektur-OnePager.pptx');
const p=Presentation.create({slideSize:{width:1600,height:900}});
const s=p.slides.add();
s.background.fill='#F8FAFC';
const c={navy:'#132B45',ink:'#20354A',muted:'#52657A',teal:'#007F86',line:'#9CADBA',light:'#EAF1F5',white:'#FFFFFF'};
function shape(name,x,y,w,h,fill='none',stroke='none'){
 return s.shapes.add({geometry:'rect',name,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1.5,style:'solid'}});
}
function text(name,value,x,y,w,h,size=26,color=c.ink,bold=false,align='left'){
 const t=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=value;
 t.text.insets=0;
 t.text.style={typeface:'Arial',fontSize:size,color,bold,alignment:align};
 return t;
}
function connect(a,b,from='right',to='left',color=c.line){
 return s.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:color,width:2.5,style:'solid'},tail:{type:'triangle',width:'sm',length:'sm'}});
}
text('title','KISS-Chris-Stack',64,47,1300,72,56,c.navy,true);
text('subtitle','Architektur für gesteuerte KI-gestützte Softwareentwicklung',66,125,1420,48,29,c.muted);

const person=shape('Entwickler',64,288,238,230,c.white,'#D3DEE6');
text('person-title','Entwickler',84,313,198,42,30,c.navy,true);
text('person-copy','Auftrag und\nAbnahmekriterien\n\nFreigabe externer\nÄnderungen',84,369,198,135,24,c.muted);

const host=shape('Agent-Host',350,215,832,352,c.white,'#C5D4DF');
shape('Agent-Header',350,215,832,85,c.navy);
text('agent-title','KI-Agent',376,229,220,44,32,c.white,true);
text('agent-sub','Codex oder Claude Code',746,239,410,35,26,c.white,false,'right');
text('routing','Globale Stack-Regeln wählen den passenden Arbeitsweg',376,315,780,35,24,c.muted);

const fast=shape('Fast Path',376,367,315,171,c.light);
text('fast-title','Fast Path',394,385,276,37,28,c.navy,true);
text('fast-body','Kleine, klare Aufgaben\nDirekte Umsetzung\nGezielte Tests',394,437,280,93,24,c.ink);

const deep=shape('Deep Path',718,367,438,171,'#E3F2F1');
text('deep-title','Deep Path mit Ouroboros',737,385,401,37,28,c.teal,true);
text('deep-body','Komplexe oder riskante Aufgaben\nSeed und Ausführung\nEvaluation und gezielte Reparatur',737,437,401,93,24,c.ink);

const result=shape('Ergebnis',1230,288,306,230,c.navy);
text('result-title','Prüfbares Ergebnis',1253,313,260,43,25,c.white,true);
text('result-copy','Codeänderungen\nTests und Nachweise\n\nAbschluss anhand der\nAbnahmekriterien',1253,369,260,135,24,c.white);
connect(person,host);
connect(host,result);

text('foundation-label','Gemeinsame Unterstützung',350,595,390,35,24,c.muted);
const foundation=shape('Unterstützende Werkzeuge',350,648,832,143,c.white,'#C5D4DF');
shape('tool-divider-1',607,670,1,96,'#D3DEE6');
shape('tool-divider-2',872,670,1,96,'#D3DEE6');
text('codegraph-title','CodeGraph',371,671,224,37,27,c.navy,true);
text('codegraph-body','Code-Struktur\nund Auswirkungen',371,719,222,62,23,c.muted);
text('ux-title','UI-UX-Pro-Max',629,671,227,37,27,c.navy,true);
text('ux-body','UI-Design\nund Accessibility',629,719,226,62,23,c.muted);
text('efficiency-title','Ponytail, Caveman, RTK',894,671,274,38,20,c.navy,true);
text('efficiency-body','Schlanker Code\nKnappe Kommunikation',894,719,266,62,23,c.muted);
connect(foundation,host,'top','bottom',c.teal);

text('visibility','Deep Path: Dashboard und unabhängiger Observer zeigen den Fortschritt',64,830,1100,34,23,c.muted);
text('budget','3 Iterationen je Kriterium   /   60 Minuten je Generation',64,867,1250,27,20,c.muted);
text('owner','Chris',1410,843,126,34,23,c.teal,true,'right');
s.speakerNotes.text='Quelle: KISS-Chris-Stack/docs/PRODUKT-ONBOARDING.md, Paketstand 2026.10.05. Die Folie verdichtet die Architektur für Management. Fast Path für lokale eindeutige Änderungen. Deep Path nutzt direkt einen Seed bei konkreten Goals, Interview/Auto nur bei Mehrdeutigkeit. Dashboard und genau ein read-only Host-Observer starten vor den Execution-Workern. Standardlimits: 3 Iterationen pro AC, 15 Minuten ohne Fortschritt und 60 Minuten je Generation. Auto-Evolution und Stage 3 sind standardmäßig deaktiviert. CodeGraph analysiert Strukturen, UI-UX-Pro-Max gilt nur für UI-Aufgaben. Ponytail reduziert Implementierungsaufwand, Caveman Agentenprosa, RTK Tool-Output. Externe Schreibaktionen benötigen menschliche Freigabe. Die Folie beschreibt den Aufbau, nicht gemessene Produktivitätseffekte. Lokale Agenten und MCP-Werkzeuge können externe Modellanbieter nutzen.';

await fs.writeFile(path.join(buildDir,'preview.png'),new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
await (await PresentationFile.exportPptx(p)).save(path.join(buildDir,'candidate.pptx'));
const {finalizePresentation}=await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')).href);
const resultValidation=await finalizePresentation({workspaceDir,candidatePath:path.join(buildDir,'candidate.pptx'),finalPath,pythonExecutable:'C:/Users/chris.sass/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-heading-fit'],explicitTotalSlideCount:1,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(buildDir,'validation-final.json')});
console.log(JSON.stringify(resultValidation));
