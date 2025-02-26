package com.example.demo.controller;

import org.springframework.web.bind.annotation.RestController;

import com.example.demo.model.Question;
import com.example.demo.service.QuestionService;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;


@RestController
@CrossOrigin
//@RequestMapping("/questions")
public class QuestionController {
	
	@Autowired
	QuestionService qservice;
	
	@PostMapping("/addques")
	public Question addques(@RequestBody Question ques) {
		qservice.addques(ques);
		
		return ques;
	}
	
	@DeleteMapping("/delques/{id}")
	public String delques(@PathVariable("id") int id)
	{
		return qservice.delques(id);
	}
	
	@DeleteMapping("/delquesmul/{ids}")
	public String delquesmul(@PathVariable("ids") List<Integer> idlist)
	{
		return qservice.delquesmul(idlist);
	}
	
	@DeleteMapping("/delquesall")
	public String delquesmul()
	{
		return qservice.delquesall();
	}
	
	@GetMapping("/getquesall")
	public ResponseEntity<List<Question>> getquesall()
	{
		return qservice.getquesall();
	}
	
	@GetMapping("/getquesByCategory/{category}")
	public List<Question> getquesByCategory(@PathVariable("category") String category)
	{
		return qservice.getquesByCategory(category);
	}
	
	@GetMapping("/getquesByCategoryAndCount")
	public List<Question> getquesByCategoryAndCount(@RequestParam String category,@RequestParam Integer count)
	{
		return qservice.getquesByCategoryAndCount(category,count);
	}

}
