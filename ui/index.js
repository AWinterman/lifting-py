import firebase from "@firebase/app"
import "@firebase/auth"
import React from "react"
import ReactDOM from "react-dom"
import Button from '@material-ui/core/Button'
import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper';
import PropTypes from 'prop-types';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Avatar from '@material-ui/core/Avatar';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import CardHeader from '@material-ui/core/CardHeader';

var config = {
  apiKey: "AIzaSyDIUCMDE_urhhCpQqEeBAmQgGWI8gOcJJg",
  authDomain: "lifting-224316.firebaseapp.com",
  databaseURL: "https://lifting-224316.firebaseio.com",
  projectId: "lifting-224316",
  storageBucket: "lifting-224316.appspot.com",
  messagingSenderId: "621199332133"
};

firebase.initializeApp(config)


class SigninButton extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      user: null,
      disabled: true
    }


    self = this

    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        self.setState({user: user, disabled: false})
      } 
    });

    firebase.auth().getRedirectResult().then(function(result) {
      var user = result.user;
      self.setState({user: user, disabled: false})
    }).catch(function(error) {
      var errorCode = error.code;
      var errorMessage = error.message;
      var email = error.email;
      var credential = error.credential;
      if (errorCode === 'auth/account-exists-with-different-credential') {
        self.setState({error: 'You have already signed up with a different auth provider for that email.'});
      } else {
        self.setState({error: 'Oops'});
      }
    });
  }

  handleClick() {
    var user = firebase.auth().currentUser
    if (!user) {
      var provider = new firebase.auth.GoogleAuthProvider();
      provider.addScope('https://www.googleapis.com/auth/plus.login');
      firebase.auth().signInWithRedirect(provider);
      this.setState({
        user: user,
        disabled: false
      })
    } else {
      firebase.auth().signOut();
      this.setState({user: null, disabled: false})
    }
  }


  render() {
    var userDetails
    if (this.state.user) {
      userDetails = (
        <>
                  <ListItem>
                    <Avatar className={this.props.avatar} src={this.state.user ? this.state.user.photoURL : ''}></Avatar>
                  </ListItem>
                  <ListItem>
                      <Typography  variant="h5" color="textSecondary">
                        {this.state.user ? this.state.user.displayName : ''}
                      </Typography>
                  </ListItem>
                  <ListItem>
                    <Typography variant="h5">{this.state.user ? this.state.user.email : ''}</Typography>
                  </ListItem>
        </>)
    } else {
      userDetails = (<></>)
    }
    return (
      <Grid  container spacing={8} justify='center' align-items='center' >
        <Grid item lg={3}>
          <Card>
            <CardHeader title="Lifting CLI Sign in" />
            <CardContent>
              <List>
                <ListItem>
                  <Typography variant="h5">{this.state.user ? "Logged in as:" : "please log in"}</Typography>
                </ListItem>
                {userDetails}
                <ListItem>
                  <Button 
                    fullWidth
                    variant="contained"
                    color="primary"
                    disabled={this.state.disabled}
                    onClick={() => this.handleClick()}>
                    {this.state.user ? "Sign out" : "Sign in"}
                  </Button>
                </ListItem>
            </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    )
  }
}


window.onload = function() {
  var button = React.createElement(SigninButton)
  ReactDOM.render(button , document.getElementById('lifting-react-container'))
}
