package com.example.demo.model;

import lombok.Data;

@Data
public class TopscoreWrapper {
	private String username;
	private Integer highscore;
	public TopscoreWrapper(String username, Integer highscore) {
		super();
		this.username = username;
		this.highscore = highscore;
	}
	
	
}
