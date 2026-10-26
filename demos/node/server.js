const express = require("express");
const app = express();
const port = process.env.PORT || 3001;
const matches = [
 {id:1,home:"Northbridge FC",away:"Coastal United",score:"2-1",status:"FT"},
 {id:2,home:"Metro Athletic",away:"Redwood Rovers",score:"1-1",status:"FT"},
 {id:3,home:"Coastal United",away:"Metro Athletic",score:"TBD",status:"UPCOMING"}
];
app.get("/", (_req,res)=>res.send("Touchline Node.js demo. Try /api/matches"));
app.get("/api/matches", (_req,res)=>res.json({source:"Node.js",matches}));
app.get("/api/matches/:id", (req,res)=>{const m=matches.find(x=>x.id===Number(req.params.id)); if(!m)return res.status(404).json({error:"Match not found"}); res.json(m);});
app.listen(port,()=>console.log(`Touchline Node API: http://localhost:${port}`));
