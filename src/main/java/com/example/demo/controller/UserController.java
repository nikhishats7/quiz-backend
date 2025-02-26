package com.example.demo.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.model.TopscoreWrapper;
import com.example.demo.model.User;
import com.example.demo.service.UserService;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.GetMapping;




@RestController
@CrossOrigin
public class UserController {
	
	@Autowired
	UserService userservice;
	
	@PostMapping("/register")
	public ResponseEntity<String> adduser(@RequestBody User user) {
		return userservice.adduser(user);
	}
	
	@PostMapping("/login")
	public ResponseEntity<String> login(@RequestBody User user) {
		return userservice.login(user);
	}
	
	@PutMapping("/updatescore")
	public ResponseEntity<String>  updatescore(@RequestParam String username, @RequestParam Integer newscore) {
		return userservice.updatescore(username, newscore);
	}
	
	@GetMapping("/getTopscorers")
	public ResponseEntity<List<TopscoreWrapper>> getTopscorers() {
		return userservice.getTopscorers();
	}
	
	

}
