package com.example.demo.dao;


import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.example.demo.model.Question;



@Repository
public interface QuestionRepo extends JpaRepository<Question, Integer>{
	List<Question> getByCategory(String category);
	
	@Query(value = "SELECT * FROM question q Where q.category = :category ORDER BY RAND() LIMIT :qnum",nativeQuery=true)
	List<Question> getRandomQuestionByCategory(String category,Integer qnum);
	//or
	List<Question> findByCategory(String category, Pageable pageable);
}
