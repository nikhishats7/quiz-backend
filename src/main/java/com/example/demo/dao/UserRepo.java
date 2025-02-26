package com.example.demo.dao;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.demo.model.TopscoreWrapper;
import com.example.demo.model.User;

@Repository
public interface UserRepo extends JpaRepository<User, Integer>{
	User findByUsername(String username);
	
	@Query(value = "SELECT DISTINCT highscore FROM User ORDER BY highscore DESC LIMIT :count",nativeQuery = true)
	List<Integer> getTopscores(Integer count);
	
	@Query(value = "SELECT username,highscore FROM User WHERE highscore IN :scores ORDER BY highscore DESC",nativeQuery = true)
	List<TopscoreWrapper> getUsersWithScores(List<Integer> scores);
}
