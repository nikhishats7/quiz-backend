package com.example.demo.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.example.demo.dao.UserRepo;
import com.example.demo.model.TopscoreWrapper;
import com.example.demo.model.User;

@Service
public class UserService {
	
	@Autowired
	UserRepo userrepo;

	public ResponseEntity<String> adduser(User user) {
		if(userrepo.findByUsername(user.getUsername())!=null)
			return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Username already exists.");
		else {
			user.setHighscore(0);
			userrepo.save(user);
			return ResponseEntity.status(HttpStatus.CREATED).body("user created");
		}
	}

	public ResponseEntity<String> login(User user) {
		User userFromdb = userrepo.findByUsername(user.getUsername());
		if(userFromdb!=null && userFromdb.getPassword().equals(user.getPassword()))
			return ResponseEntity.ok("login successfull");
		else 
			return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("invalid credentials");
	}

	public ResponseEntity<String> updatescore(String username, Integer newscore) {
		User user = userrepo.findByUsername(username);
		if(user == null)
			return ResponseEntity.status(HttpStatus.NOT_FOUND).body("user not exist");
		if(newscore > user.getHighscore())
		{
			user.setHighscore(newscore);
			userrepo.save(user);
		}
		return ResponseEntity.ok("score updated");
		
	}

	public ResponseEntity<List<TopscoreWrapper>> getTopscorers() {
		List<Integer> top2scores = userrepo.getTopscores(2);
		List<TopscoreWrapper> usernames = userrepo.getUsersWithScores(top2scores);
		return ResponseEntity.status(HttpStatus.OK).body(usernames);
	}
	

}
