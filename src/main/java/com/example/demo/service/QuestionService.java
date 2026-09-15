package com.example.demo.service;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.example.demo.dao.QuestionRepo;
import com.example.demo.model.Question;

@Service
public class QuestionService {
	
	@Autowired
	QuestionRepo qrepo;
	
	@CacheEvict(cacheNames = {"allQuestions", "questionsByCategory"}, allEntries = true)
	public Question addques(Question ques)
	{
		qrepo.save(ques);
		return ques;
	}
	
	@CacheEvict(cacheNames = {"allQuestions", "questionsByCategory"}, allEntries = true)
	public String delques(int id)
	{
		qrepo.deleteById(id);;
		return "deleted"+id;
	}
	
	@CacheEvict(cacheNames = {"allQuestions", "questionsByCategory"}, allEntries = true)
	public String delquesmul(List<Integer> ids)
	{
		qrepo.deleteAllById(ids);
		return "deleted"+ids;
	}
	
	@CacheEvict(cacheNames = {"allQuestions", "questionsByCategory"}, allEntries = true)
	public String delquesall()
	{
		qrepo.deleteAll();
		return "all deleted";
	}
	
	@Cacheable(cacheNames = "allQuestions")
	public List<Question> getquesall()
	{
		return qrepo.findAll();
	}
	
	@Cacheable(cacheNames = "questionsByCategory", key = "#category")
	public List<Question> getquesByCategory(String category)
	{
		return qrepo.getByCategory(category);

	}

	public List<Question> getquesByCategoryAndCount(String category, Integer count) {
//		return qrepo.findByCategory(category, PageRequest.of(0, count)); //or
		return qrepo.getRandomQuestionByCategory(category, count);
	}

}
