//package com.example.demo.controller;
//
//import java.util.List;
//
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.http.ResponseEntity;
//import org.springframework.web.bind.annotation.GetMapping;
//import org.springframework.web.bind.annotation.PathVariable;
//import org.springframework.web.bind.annotation.RestController;
//
//import com.example.demo.model.QuestionWrapper;
//import com.example.demo.model.Quiz;
//import com.example.demo.model.answerFromUser;
//import com.example.demo.service.QuizService;
//
//import org.springframework.web.bind.annotation.PostMapping;
//import org.springframework.web.bind.annotation.RequestBody;
//import org.springframework.web.bind.annotation.RequestParam;
//
//
//@RestController
//public class QuizController {
//	@Autowired
//	QuizService quizservice;
//
//	@PostMapping("/addquiz")
//	public String createquiz(@RequestParam String category,@RequestParam Integer qnum ,@RequestParam String title) {
//		return quizservice.createquiz(category,qnum,title);
//		
//	}
//	
//	@GetMapping("/getquiz/{id}")
//	public ResponseEntity<List<QuestionWrapper>> getquiz(@PathVariable("id") Integer id)
//	{
//		return quizservice.getquiz(id);
//	}
//	
//	@GetMapping("/getresultOfQuiz/{id}")
//	public ResponseEntity<Integer> getresultOfQuiz(@PathVariable("id") Integer id,@RequestBody List<answerFromUser> answerFromUsers)
//	{
//		return quizservice.getresultOfQuiz(id,answerFromUsers);
//	}
//}
//
//
//
