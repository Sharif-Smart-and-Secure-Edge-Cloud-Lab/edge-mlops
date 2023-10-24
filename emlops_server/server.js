// Importing Libraies that we installed using npm
const express = require("express")
const app = express()
const bcrypt = require("bcrypt")
const passport = require("passport")
// const initializePassport = require("./passport-config")
const LocalStrategy = require("passport-local").Strategy
const flash = require("express-flash")
const session = require("express-session")
const methodOverride = require("method-override")
const mongoose = require("mongoose")
const { name } = require("ejs")
const path = require('path')
const WebSocket = require('ws')
const { spawn } = require('child_process');

function initialize(passport, getUserByEmail, getUserById){
    // Function to authenticate users
    const authenticateUsers = async (email, password, done) => {
        // Get users by email
        const user = await User.findOne({email: email});
        if (user == null){
            return done(null, false, {message: "No user found with that email"})
        }
        try {
            if(await bcrypt.compare(password, user.password)){
                console.log(user.name + " loged in");
                return done(null, user)
            } else{
                return done (null, false, {message: "Password Incorrect"})
            }
        } catch (e) {
            console.log(e);
            return done(e)
        }
    }
    passport.use(new LocalStrategy({usernameField: 'email'}, authenticateUsers))
    passport.serializeUser((user, done) => done(null, user._id))
    passport.deserializeUser((id, done) => {
        return done(null,id)
    })
}

initialize(passport,email => user.email ,id => user._id)

const userSchema = new mongoose.Schema({
    name : {type: String , required: true},
    email :  {type: String , required: true},
    password : {type: String , required: true},
    date: {type: Date , default: Date.now}
})
const User = mongoose.model('User',userSchema);
async function createUser(name,email,password){
    const user = new User({
        name: name,
        email : email,
        password: password
    });
    const result = await user.save();
    console.log(result);
}

app.use(express.urlencoded({extended: false}))
app.use(flash())
app.use(session({
    secret: 'secret',
    resave: false,
    saveUninitialized: false
}))
app.use(passport.initialize()) 
app.use(passport.session())
app.use(methodOverride("_method"))
app.use(express.static('public'));

// Configuring the register post functionality
app.post("/login", checkNotAuthenticated, passport.authenticate("local", {
    successRedirect: "/",
    failureRedirect: "/login",
    failureFlash: true
}))

// Configuring the register post functionality
app.post("/register", checkNotAuthenticated, async (req, res) => {

    try {
        const hashedPassword = await bcrypt.hash(req.body.password, 10)
        createUser(req.body.name,req.body.email,hashedPassword);
        res.redirect("/login")
    } catch (e) {
        console.log(e);
        res.redirect("/register")
    }
})

// Routes
app.get('/', async (req, res) => {
    if(req.isAuthenticated()){
        const name = await getUserName(req.session.passport.user);
        res.render("homepage_logedin.ejs", {name: name , background: '/images/homepage3.png', describe: '/images/describe.png' , face:'/images/face.png' , voice: '/images/voice.jpg' , sensor: '/images/sensor.png', fahim:'/images/fahim.jpg' , rahdar:'/images/rahdar.jpg', samadi:'/images/samadi.jpg', abedi:'/images/abedi.jpg' , sharif:'/images/sharif.png'})
    }
    else{
        res.render("homepage_not_login.ejs", {background: '/images/homepage3.png', describe: '/images/describe.png' , face:'/images/face.png' , voice: '/images/voice.jpg' , sensor: '/images/sensor.png', fahim:'/images/fahim.jpg' , rahdar:'/images/rahdar.jpg', samadi:'/images/samadi.jpg', abedi:'/images/abedi.jpg' , sharif:'/images/sharif.png'})
    }
})

app.get('/login', checkNotAuthenticated, (req, res) => {
    console.log(req.originalUrl);
    res.render("login.ejs",{background: '/images/homepage3.png' })
})

app.get('/register', checkNotAuthenticated, (req, res) => {
    res.render("register.ejs", {background: '/images/homepage3.png' })
})

app.get('/training', checkAuthenticated, async (req, res) => {
    const name = await getUserName(req.session.passport.user);
    res.render("Dashboard.ejs", {name: name, background: '/images/dashboard.png'} )
})

app.get('/Training/NewTrain', checkAuthenticated, async (req, res) => {
    const name = await getUserName(req.session.passport.user);
    res.render("New_Train.ejs", {name: name, background: '/images/dashboard.png'} )
})
// End Routes

app.delete("/logout", async(req, res) => { 
    const name = await getUserName(req.session.passport.user);
    req.logout(req.user, async err => {
        if (err){
            console.log(err);
            return next(err)
        }
        console.log(name + ' loged out')
        res.redirect("/")
    })
})

function checkAuthenticated(req, res, next){
    if(req.isAuthenticated()){
        return next()
    }
    res.redirect("/login")
}

function checkNotAuthenticated(req, res, next){
    if(req.isAuthenticated()){
        return res.redirect("/")
    }
    next()
}
async function getUserName(id){
    const user = await User.findOne({_id: id}); 
    return user.name; 
}

const wss = new WebSocket.Server({port: '8080'} , ()=> console.log("Websocket is listening to 8080"));

wss.on('connection' , ws=>{
    ws.on('message' , data =>{
        if(ws.readyState !== ws.OPEN) return
        connectedClients.push(ws)
    });
});


const pythonProcess = spawn('../../edge_env/Scripts/python', ['../imdb_model/Server.py']);
pythonProcess.stdout.on('data', (data) => {
    console.log(`Python module output: ${data}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python module error: ${data}`);
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Python module exited with code ${code}`);
  });


app.listen(3000 , () =>{
    mongoose.connect('mongodb://127.0.0.1:27017/Edge_MLOps',{
        useNewUrlParser: true,
        useUnifiedTopology: true
    }).then(db => console.log('connected to db')).catch(err => console.log(err))
})